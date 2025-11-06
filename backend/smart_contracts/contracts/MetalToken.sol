// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Imports
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "../interfaces/IMetalToken.sol";
import "../libraries/SecurityUtils.sol";

/**
 * @title MetalToken
 * @dev Metal Token Contract - Oltin, kumush, platina, palladiy uchun
 */
contract MetalToken is IMetalToken, ERC20, ERC20Burnable, ERC20Pausable, AccessControl {
    using SecurityUtils for uint256;
    
    // Roles
    bytes32 public constant METAL_ADMIN_ROLE = keccak256("METAL_ADMIN_ROLE");
    bytes32 public constant PRICE_ORACLE_ROLE = keccak256("PRICE_ORACLE_ROLE");
    bytes32 public constant STORAGE_MANAGER_ROLE = keccak256("STORAGE_MANAGER_ROLE");
    bytes32 public constant PHYSICAL_DEPOSIT_ROLE = keccak256("PHYSICAL_DEPOSIT_ROLE");
    
    // State variables
    mapping(MetalType => MetalInfo) private _metalInfo;
    mapping(address => StorageInfo) private _storageInfo;
    mapping(MetalType => MetalBalance) private _metalBalances;
    mapping(address => mapping(MetalType => uint256)) private _physicalHoldings;
    
    address[] private _activeStorages;
    uint256 private _storageCount = 0;
    
    // Constants
    uint256 private constant OUNCE_TO_GRAMS = 31103; // 1 troy ounce = 31.103 grams
    uint256 private constant METAL_DECIMALS = 6; // 6 decimal places for precision
    
    // Events
    event MetalAdded(MetalType indexed metal, string symbol, string name, uint256 purity);
    event StorageAdded(address indexed storage, string name, uint256 capacity);
    event PhysicalDeposit(address indexed metal, address indexed storage, address indexed depositor, uint256 amount);
    event PhysicalWithdrawal(address indexed metal, address indexed storage, address indexed withdrawer, uint256 amount);
    event MetalPriceUpdated(MetalType indexed metal, uint256 pricePerOunce, uint256 timestamp);
    event StorageVerified(address indexed storage, bool verified);
    event PhysicalTransfer(address indexed fromStorage, address indexed toStorage, MetalType indexed metal, uint256 amount);
    
    // Custom errors
    error MetalAlreadySupported(MetalType metal);
    error MetalNotSupported(MetalType metal);
    error StorageAlreadyExists(address storage);
    error StorageNotFound(address storage);
    error InvalidStorageCapacity(uint256 capacity);
    error InvalidMetalAmount(uint256 amount);
    error InsufficientPhysicalBalance(MetalType metal, address storage, uint256 requested, uint256 available);
    error InvalidPrice(uint256 price);
    error StorageNotVerified(address storage);
    error TransferToSameStorage(address from, address to);
    error InvalidPurity(uint256 purity);
    error OracleNotSet(MetalType metal);
    
    /**
     * @dev Constructor
     */
    constructor() ERC20("METALS", "METALS") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(METAL_ADMIN_ROLE, msg.sender);
        _grantRole(PRICE_ORACLE_ROLE, msg.sender);
        _grantRole(STORAGE_MANAGER_ROLE, msg.sender);
        _grantRole(PHYSICAL_DEPOSIT_ROLE, msg.sender);
        
        // Initialize supported metals
        _initializeMetals();
    }
    
    /**
     * @dev Mint tokens (digital representation)
     */
    function mint(address to, uint256 amount) external override onlyRole(METAL_ADMIN_ROLE) returns (bool) {
        require(to != address(0), "Cannot mint to zero address");
        require(amount > 0, "Cannot mint zero amount");
        
        _mint(to, amount);
        
        emit MetalTokensMinted(to, amount);
        return true;
    }
    
    /**
     * @dev Burn tokens (for redemption)
     */
    function burn(address from, uint256 amount) external override onlyRole(METAL_ADMIN_ROLE) returns (bool) {
        require(from != address(0), "Cannot burn from zero address");
        require(amount > 0, "Cannot burn zero amount");
        require(balanceOf(from) >= amount, "Insufficient balance");
        
        _burn(from, amount);
        
        emit MetalTokensBurned(from, amount);
        return true;
    }
    
    /**
     * @dev Deposit physical metal to storage
     */
    function depositPhysical(MetalType metal, uint256 amount, address storage) 
        external override whenNotPaused onlyRole(PHYSICAL_DEPOSIT_ROLE) {
        require(amount > 0, "Amount must be positive");
        
        StorageInfo storage storageInfo = _storageInfo[storage];
        if (storageInfo.storage == address(0)) {
            revert StorageNotFound(storage);
        }
        
        if (!storageInfo.verified) {
            revert StorageNotVerified(storage);
        }
        
        // Update physical holdings
        _physicalHoldings[storage][metal] = _physicalHoldings[storage][metal].safeAdd(amount);
        _physicalHoldings[address(0)][metal] = _physicalHoldings[address(0)][metal].safeAdd(amount); // Global total
        
        // Update storage info
        storageInfo.currentHoldings = storageInfo.currentHoldings.safeAdd(amount);
        
        // Update global metal balance
        _metalBalances[metal].physical = _metalBalances[metal].physical.safeAdd(amount);
        _metalBalances[metal].lastUpdate = block.timestamp;
        
        emit PhysicalDeposit(address(uint160(metal)), storage, msg.sender, amount);
    }
    
    /**
     * @dev Withdraw physical metal from storage
     */
    function withdrawPhysical(MetalType metal, uint256 amount, address storage) 
        external override whenNotPaused onlyRole(PHYSICAL_DEPOSIT_ROLE) {
        require(amount > 0, "Amount must be positive");
        
        StorageInfo storage storageInfo = _storageInfo[storage];
        if (storageInfo.storage == address(0)) {
            revert StorageNotFound(storage);
        }
        
        uint256 availableBalance = _physicalHoldings[storage][metal];
        if (availableBalance < amount) {
            revert InsufficientPhysicalBalance(metal, storage, amount, availableBalance);
        }
        
        // Update physical holdings
        _physicalHoldings[storage][metal] = availableBalance.safeSub(amount);
        _physicalHoldings[address(0)][metal] = _physicalHoldings[address(0)][metal].safeSub(amount); // Global total
        
        // Update storage info
        storageInfo.currentHoldings = storageInfo.currentHoldings.safeSub(amount);
        
        // Update global metal balance
        _metalBalances[metal].physical = _metalBalances[metal].physical.safeSub(amount);
        _metalBalances[metal].lastUpdate = block.timestamp;
        
        emit PhysicalWithdrawal(address(uint160(metal)), storage, msg.sender, amount);
    }
    
    /**
     * @dev Update metal price
     */
    function updatePrice(MetalType metal, uint256 pricePerOunce) external override {
        require(hasRole(PRICE_ORACLE_ROLE, msg.sender), "Oracle role required");
        require(pricePerOunce > 0, "Price must be positive");
        
        MetalInfo storage metalInfo = _metalInfo[metal];
        if (metalInfo.metal == MetalType(0)) {
            revert MetalNotSupported(metal);
        }
        
        uint256 oldPrice = metalInfo.currentPrice;
        metalInfo.currentPrice = pricePerOunce;
        metalInfo.lastUpdate = block.timestamp;
        
        emit MetalPriceUpdated(metal, pricePerOunce, block.timestamp);
    }
    
    /**
     * @dev Add a new storage facility
     */
    function addStorage(address storage, string memory name, uint256 capacity) 
        external override onlyRole(STORAGE_MANAGER_ROLE) {
        require(storage != address(0), "Invalid storage address");
        require(capacity > 0, "Capacity must be positive");
        require(_storageInfo[storage].storage == address(0), "Storage already exists");
        
        _storageInfo[storage] = StorageInfo({
            storage: storage,
            name: name,
            capacity: capacity,
            currentHoldings: 0,
            verified: false,
            active: true
        });
        
        _activeStorages.push(storage);
        _storageCount++;
        
        emit StorageAdded(storage, name, capacity);
    }
    
    /**
     * @dev Verify storage facility
     */
    function verifyStorage(address storage, bool verified) external onlyRole(STORAGE_MANAGER_ROLE) {
        StorageInfo storage storageInfo = _storageInfo[storage];
        if (storageInfo.storage == address(0)) {
            revert StorageNotFound(storage);
        }
        
        storageInfo.verified = verified;
        emit StorageVerified(storage, verified);
    }
    
    /**
     * @dev Transfer metal between storages
     */
    function transferBetweenStorages(
        address fromStorage,
        address toStorage,
        MetalType metal,
        uint256 amount
    ) external override onlyRole(STORAGE_MANAGER_ROLE) {
        require(fromStorage != toStorage, "Cannot transfer to same storage");
        
        StorageInfo storage fromStorageInfo = _storageInfo[fromStorage];
        StorageInfo storage toStorageInfo = _storageInfo[toStorage];
        
        if (fromStorageInfo.storage == address(0)) {
            revert StorageNotFound(fromStorage);
        }
        
        if (toStorageInfo.storage == address(0)) {
            revert StorageNotFound(toStorage);
        }
        
        uint256 fromBalance = _physicalHoldings[fromStorage][metal];
        if (fromBalance < amount) {
            revert InsufficientPhysicalBalance(metal, fromStorage, amount, fromBalance);
        }
        
        // Transfer metal
        _physicalHoldings[fromStorage][metal] = fromBalance.safeSub(amount);
        _physicalHoldings[toStorage][metal] = _physicalHoldings[toStorage][metal].safeAdd(amount);
        
        // Update storage holdings
        fromStorageInfo.currentHoldings = fromStorageInfo.currentHoldings.safeSub(amount);
        toStorageInfo.currentHoldings = toStorageInfo.currentHoldings.safeAdd(amount);
        
        emit PhysicalTransfer(fromStorage, toStorage, metal, amount);
    }
    
    /**
     * @dev Update metal price (alias for updatePrice)
     */
    function updateMetalPrice(MetalType metal, uint256 pricePerOunce) external override {
        updatePrice(metal, pricePerOunce);
    }
    
    /**
     * @dev Convert metal amount to USD value
     */
    function convertPrice(MetalType metal, uint256 amount) external view override returns (uint256 usdValue) {
        MetalInfo storage metalInfo = _metalInfo[metal];
        if (metalInfo.currentPrice == 0) {
            return 0;
        }
        
        uint256 ounces = gramsToOunces(amount);
        usdValue = ounces.safeMul(metalInfo.currentPrice);
        
        return usdValue;
    }
    
    /**
     * @dev Get storage information
     */
    function getStorageInfo(address storage) external view override returns (StorageInfo memory) {
        return _storageInfo[storage];
    }
    
    /**
     * @dev Get metal holdings in a storage
     */
    function getStorageHoldings(address storage) external view override returns (uint256) {
        return _storageInfo[storage].currentHoldings;
    }
    
    /**
     * @dev Get metal information
     */
    function getMetalInfo(MetalType metal) external view override returns (MetalInfo memory) {
        return _metalInfo[metal];
    }
    
    /**
     * @dev Get metal balance (physical and digital)
     */
    function getMetalBalance(MetalType metal) external view override returns (MetalBalance memory) {
        return _metalBalances[metal];
    }
    
    /**
     * @dev Get metal price per ounce
     */
    function getMetalPrice(MetalType metal) external view override returns (uint256) {
        return _metalInfo[metal].currentPrice;
    }
    
    /**
     * @dev Get all supported metals
     */
    function getSupportedMetals() external view override returns (MetalInfo[] memory) {
        MetalType[] memory metalTypes = new MetalType[](4);
        metalTypes[0] = MetalType.GOLD;
        metalTypes[1] = MetalType.SILVER;
        metalTypes[2] = MetalType.PLATINUM;
        metalTypes[3] = MetalType.PALLADIUM;
        
        MetalInfo[] memory metals = new MetalInfo[](4);
        for (uint256 i = 0; i < 4; i++) {
            metals[i] = _metalInfo[metalTypes[i]];
        }
        
        return metals;
    }
    
    /**
     * @dev Get active storage facilities
     */
    function getActiveStorages() external view override returns (address[] memory) {
        return _activeStorages;
    }
    
    /**
     * @dev Convert ounces to grams
     */
    function ouncesToGrams(uint256 ounces) external pure override returns (uint256 grams) {
        return ounces.safeMul(OUNCE_TO_GRAMS);
    }
    
    /**
     * @dev Convert grams to ounces
     */
    function gramsToOunces(uint256 grams) external pure override returns (uint256 ounces) {
        return grams.safeDiv(OUNCE_TO_GRAMS);
    }
    
    /**
     * @dev Calculate total value of metal holdings
     */
    function calculateValue(MetalType metal, uint256 amount) external view override returns (uint256 usdValue) {
        MetalInfo storage metalInfo = _metalInfo[metal];
        if (metalInfo.currentPrice == 0) {
            return 0;
        }
        
        return convertPrice(metal, amount);
    }
    
    /**
     * @dev Set price oracle for a metal
     */
    function setPriceOracle(MetalType metal, address oracle) external override onlyRole(METAL_ADMIN_ROLE) {
        require(oracle != address(0), "Invalid oracle address");
        
        MetalInfo storage metalInfo = _metalInfo[metal];
        if (metalInfo.metal == MetalType(0)) {
            revert MetalNotSupported(metal);
        }
        
        // In a real implementation, you'd store the oracle address
        emit OracleSet(metal, oracle);
    }
    
    /**
     * @dev Update price from oracle
     */
    function updatePriceFromOracle(MetalType metal) external override {
        MetalInfo storage metalInfo = _metalInfo[metal];
        if (metalInfo.metal == MetalType(0)) {
            revert MetalNotSupported(metal);
        }
        
        // This would interact with actual oracle
        // For now, we'll assume oracle calls updatePrice directly
        revert OraclePriceUpdateNotImplemented();
    }
    
    /**
     * @dev Pause contract
     */
    function pause() external onlyRole(METAL_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyRole(METAL_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Initialize supported metals
     */
    function _initializeMetals() internal {
        // Gold
        _metalInfo[MetalType.GOLD] = MetalInfo({
            metal: MetalType.GOLD,
            symbol: "XAU",
            name: "Gold",
            purity: 999,
            weightPerUnit: 31103, // 1 troy ounce in grams
            currentPrice: 0,
            lastUpdate: 0,
            active: true
        });
        
        // Silver
        _metalInfo[MetalType.SILVER] = MetalInfo({
            metal: MetalType.SILVER,
            symbol: "XAG",
            name: "Silver",
            purity: 999,
            weightPerUnit: 31103, // 1 troy ounce in grams
            currentPrice: 0,
            lastUpdate: 0,
            active: true
        });
        
        // Platinum
        _metalInfo[MetalType.PLATINUM] = MetalInfo({
            metal: MetalType.PLATINUM,
            symbol: "XPT",
            name: "Platinum",
            purity: 999,
            weightPerUnit: 31103,
            currentPrice: 0,
            lastUpdate: 0,
            active: true
        });
        
        // Palladium
        _metalInfo[MetalType.PALLADIUM] = MetalInfo({
            metal: MetalType.PALLADIUM,
            symbol: "XPD",
            name: "Palladium",
            purity: 999,
            weightPerUnit: 31103,
            currentPrice: 0,
            lastUpdate: 0,
            active: true
        });
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
    error MetalTokensMinted(address indexed to, uint256 amount);
    error MetalTokensBurned(address indexed from, uint256 amount);
    error OracleSet(MetalType indexed metal, address indexed oracle);
    error OraclePriceUpdateNotImplemented();
    
    /**
     * @dev Additional events
     */
    event MetalTokensMinted(address indexed to, uint256 amount);
    event MetalTokensBurned(address indexed from, uint256 amount);
    event OracleSet(MetalType indexed metal, address indexed oracle);
}