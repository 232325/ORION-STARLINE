// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

/**
 * @title MainContract
 * @dev Asosiy smart contract - deployment va testing uchun namuna
 * @author Deployment Testing System
 */
contract MainContract is Ownable, Pausable, ReentrancyGuard {
    
    // Events
    event TokensMinted(address indexed to, uint256 amount);
    event TokensBurned(address indexed from, uint256 amount);
    event AdminAdded(address indexed admin);
    event AdminRemoved(address indexed admin);
    event Paused(address account);
    event Unpaused(address account);
    
    // State variables
    bool public initialized;
    uint256 public totalSupply;
    uint256 public constant MAX_SUPPLY = 1000000000 * 10**18; // 1B tokens
    
    // Mappings
    mapping(address => bool) public admins;
    mapping(address => uint256) public balances;
    mapping(address => mapping(address => uint256)) public allowances;
    
    // Modifiers
    modifier onlyAdmin() {
        require(admins[msg.sender] || msg.sender == owner(), "Not authorized");
        _;
    }
    
    modifier whenNotPaused() {
        require(!paused(), "Contract is paused");
        _;
    }
    
    // Constructor
    constructor() {
        initialized = true;
        _transferOwnership(msg.sender);
    }
    
    /**
     * @dev Initialize contract with initial supply
     */
    function initialize(uint256 _initialSupply) external onlyOwner {
        require(!initialized, "Already initialized");
        require(_initialSupply <= MAX_SUPPLY, "Supply exceeds maximum");
        
        initialized = true;
        totalSupply = _initialSupply;
        balances[msg.sender] = _initialSupply;
        
        emit TokensMinted(msg.sender, _initialSupply);
    }
    
    /**
     * @dev Mint tokens
     * @param to Address to mint tokens to
     * @param amount Amount of tokens to mint
     */
    function mintTokens(address to, uint256 amount) 
        external 
        onlyOwner 
        whenNotPaused 
    {
        require(to != address(0), "Invalid address");
        require(amount > 0, "Amount must be positive");
        require(totalSupply + amount <= MAX_SUPPLY, "Exceeds max supply");
        
        totalSupply += amount;
        balances[to] += amount;
        
        emit TokensMinted(to, amount);
    }
    
    /**
     * @dev Burn tokens
     * @param amount Amount of tokens to burn
     */
    function burn(uint256 amount) external whenNotPaused {
        require(amount > 0, "Amount must be positive");
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        totalSupply -= amount;
        
        emit TokensBurned(msg.sender, amount);
    }
    
    /**
     * @dev Transfer tokens
     * @param to Recipient address
     * @param amount Amount to transfer
     */
    function transfer(address to, uint256 amount) 
        external 
        whenNotPaused 
        nonReentrant 
        returns (bool) 
    {
        return _transfer(msg.sender, to, amount);
    }
    
    /**
     * @dev Transfer from approved address
     */
    function transferFrom(address from, address to, uint256 amount) 
        external 
        whenNotPaused 
        nonReentrant 
        returns (bool) 
    {
        require(allowances[from][msg.sender] >= amount, "Insufficient allowance");
        
        allowances[from][msg.sender] -= amount;
        _transfer(from, to, amount);
        
        return true;
    }
    
    /**
     * @dev Approve spender to spend tokens
     */
    function approve(address spender, uint256 amount) external whenNotPaused returns (bool) {
        require(spender != address(0), "Invalid spender");
        
        allowances[msg.sender][spender] = amount;
        return true;
    }
    
    /**
     * @dev Internal transfer function
     */
    function _transfer(address from, address to, uint256 amount) internal returns (bool) {
        require(to != address(0), "Invalid recipient");
        require(balances[from] >= amount, "Insufficient balance");
        
        balances[from] -= amount;
        balances[to] += amount;
        
        return true;
    }
    
    /**
     * @dev Add admin
     */
    function addAdmin(address account) external onlyOwner {
        require(account != address(0), "Invalid address");
        require(!admins[account], "Already admin");
        
        admins[account] = true;
        emit AdminAdded(account);
    }
    
    /**
     * @dev Remove admin
     */
    function removeAdmin(address account) external onlyOwner {
        require(admins[account], "Not admin");
        
        admins[account] = false;
        emit AdminRemoved(account);
    }
    
    /**
     * @dev Pause contract
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Emergency withdraw (owner only)
     */
    function emergencyWithdraw() external onlyOwner nonReentrant {
        uint256 balance = address(this).balance;
        require(balance > 0, "No balance to withdraw");
        
        payable(msg.sender).transfer(balance);
    }
    
    /**
     * @dev Simple function for testing
     */
    function simpleOperation() external whenNotPaused {
        // Simple operation for testing
        emit TokensMinted(msg.sender, 0);
    }
    
    /**
     * @dev Complex operation with multiple steps
     */
    function complexOperation(address to, uint256 amount) 
        external 
        whenNotPaused 
        onlyAdmin 
        nonReentrant 
    {
        require(to != address(0), "Invalid address");
        require(amount > 0, "Amount must be positive");
        
        // Step 1: Mint tokens
        if (totalSupply + amount <= MAX_SUPPLY) {
            totalSupply += amount;
            balances[to] += amount;
            emit TokensMinted(to, amount);
        }
        
        // Step 2: Transfer from admin
        if (balances[msg.sender] >= amount) {
            balances[msg.sender] -= amount;
            balances[to] += amount;
        }
        
        // Step 3: Emit event
        emit TokensMinted(msg.sender, 0);
    }
    
    /**
     * @dev View functions for testing
     */
    function getBalance(address account) external view returns (uint256) {
        return balances[account];
    }
    
    function getAllowance(address owner, address spender) external view returns (uint256) {
        return allowances[owner][spender];
    }
    
    function isAdmin(address account) external view returns (bool) {
        return admins[account];
    }
    
    /**
     * @dev Get contract version
     */
    function version() external pure returns (string memory) {
        return "1.0.0";
    }
    
    /**
     * @dev Fallback function
     */
    receive() external payable {
        // Accept ETH payments
    }
    
    /**
     * @dev Emergency function for testing errors
     */
    function operationWithRevert() external pure {
        revert("Operation not allowed");
    }
    
    /**
     * @dev Store data for testing (for performance tests)
     */
    mapping(uint256 => string) public storedData;
    
    function storeData(uint256 key, string memory value) external {
        storedData[key] = value;
    }
    
    function getData(uint256 key) external view returns (string memory) {
        return storedData[key];
    }
    
    /**
     * @dev Tight packing for gas optimization testing
     */
    struct TightPacked {
        uint128 value1;
        uint64 value2;
        uint32 value3;
        uint8 value4;
    }
    
    mapping(uint256 => TightPacked) public packedData;
    
    function storeTightPacked(uint256 key, uint8 value4) external {
        packedData[key].value1 = 1000;
        packedData[key].value2 = 100;
        packedData[key].value3 = 10;
        packedData[key].value4 = value4;
    }
    
    /**
     * @dev Sparse storage for testing storage optimization
     */
    mapping(uint256 => uint256) public sparseData;
    
    function storeSparse(uint256 key, uint256 value) external {
        sparseData[key] = value;
    }
    
    /**
     * @dev Batch operations for testing
     */
    function batchTransfer(address[] memory recipients, uint256[] memory amounts) 
        external 
        whenNotPaused 
        nonReentrant 
    {
        require(recipients.length == amounts.length, "Array length mismatch");
        require(recipients.length <= 100, "Too many recipients");
        
        for (uint256 i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "Invalid recipient");
            require(amounts[i] > 0, "Amount must be positive");
            require(balances[msg.sender] >= amounts[i], "Insufficient balance");
            
            balances[msg.sender] -= amounts[i];
            balances[recipients[i]] += amounts[i];
        }
    }
}